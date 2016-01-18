from AbstractStrategy import AbstractStrategy
from Bot.param import *


class MyStrategy(AbstractStrategy):
    def __init__(self, game):
        AbstractStrategy.__init__(self, game)
        # Insert game into MyStrategy
        self._actions = ['left', 'right', 'turnleft', 'turnright', 'down', 'drop']

    def choose(self):
        game = self._game
        currentField, currentPiece, currentPiecePosition = game.me.field.field, game.piece._name, game.piecePosition
        nextPiece = game.nextPiece._name
        fieldWidth, fieldHeight = game.me.field.width, game.me.field.height
        skips = game.me.skips
        fakeComplete = 0
        bestScore = -9999
        for f in currentField:
            if sum(f) == 30:
                fakeComplete += 1
        
        for row in range(fieldHeight):
            for col in range(fieldWidth):
                if currentField[row][col] == 0 or currentField[row][col] == 1:
                    currentField[row][col] = 0
                else:
                    currentField[row][col] = 1
        col_topRow, col_holeRow, peekRow = find_col_top_and_available_hole(currentField, fieldWidth, fieldHeight)
        available_and_score = find_available_place_return_field(currentField, currentPiece, fieldWidth, fieldHeight, col_topRow, fakeComplete)
        for obj in available_and_score:
        	new_field = obj[3]
        	# place, dir,new_score, new_field
        	new_col_topRow, new_col_holeRow, new_peekRow = find_col_top_and_available_hole(new_field, fieldWidth, fieldHeight)
        	new_available_and_score = find_available_place(new_field, nextPiece, fieldWidth, fieldHeight, new_col_topRow, fakeComplete)
        	new_available_and_score = sorted(new_available_and_score, key=lambda tup: tup[2], reverse=True)
        	obj[2] += (new_available_and_score[0][2] + new_available_and_score[1][2]) / 2
        available_and_score = sorted(available_and_score, key=lambda tup: tup[2], reverse=True)
        for idx, result in enumerate(available_and_score):
            is_available, moves = back_to_forward(currentField, result[0], result[1], currentPiece)
            if is_available:
                bestScore = result[2]
                break

        if skips > 0 and bestScore < -80:
            return ['skip']
        return moves
        
        
# util

# Backtrace
def back_to_forward(field, top_point, block_rotation_state, piece):
    field[0][3], field[0][4], field[0][5], field[0][6] = 0, 0, 0, 0
    top_point = (top_point[1], top_point[0])

    move = back_trace_move(field,top_point, block_rotation_state, piece)
    if not move:
        return (False, [])
    new_move = []
    for i in xrange(len(move)-1, -1, -1):
        # up -> down left -> right right -> left turnleft -> turnright turnright -> turnleft
        if move[i] == 'up':
            new_move.append('down')
        elif move[i] == 'left':
            new_move.append('right')
        elif move[i] == 'right':
            new_move.append('left')
        elif move[i] == 'turnleft':
            new_move.append('turnright')
        elif move[i] == 'turnright':
            new_move.append('turnleft')
        else:
            print 'new_move.append error'
    '''
    for index in xrange(len(new_move)-1, -1, -1):
        if new_move[index] != 'down':
            break
        else:
            new_move.pop()
        new_move.append('drop')
    '''
    return (True, new_move)

def back_trace_move(field,  top_point, block_rotation_state, piece):
    if not check_block_legal(field, top_point, block_rotation_state, piece):
        print 'block is going to fill an already filled space'
        return []
    back_move = [((top_point, block_rotation_state), [])]
    state_history = [(top_point, block_rotation_state)]
    # Back move: up, left, right, turnleft, turnright
    while back_move:
        (currentTop, currentBlockState), move_history = back_move.pop(0)
        for (actionTop, actionBlockState), action in get_successors(field, currentTop, currentBlockState, piece):
            if not (actionTop, actionBlockState) in state_history:
                new_move_history = move_history[:]
                new_move_history.append(action)
                if check_goal(actionTop, actionBlockState, piece):
                    return new_move_history
                back_move.append(((actionTop,actionBlockState), new_move_history))
                state_history.append((actionTop, actionBlockState))
    return []

def check_goal(top, block_rotation_state, piece):
    goalTop = (4, -1) if piece == 'O' else (3, -1)
    return top == goalTop and block_rotation_state == 0

def get_successors(field, top, block_rotation_state, piece):
    legal_back_move = ['up', 'left', 'right', 'turnleft', 'turnright'] if not piece == 'O' else ['up', 'left', 'right']
    to_return = []
    for action in legal_back_move:
        if check_move_legal(field, top, block_rotation_state, action, piece):
            to_return.append((get_action_top_rotate_state(top, block_rotation_state, action, piece), action))
    # ((top[0], top[1]), block_rotation_state), action
    return to_return


def get_action_top_rotate_state(top, block_rotation_state, action, piece):
    if action == 'up':
        return ((top[0], top[1]-1), block_rotation_state)
    elif action == 'left':
        return ((top[0]-1, top[1]), block_rotation_state)
    elif action == 'right':
        return ((top[0]+1, top[1]), block_rotation_state)
    elif action == 'turnleft':
        if block_rotation_state + 1 > len(d_piece_to_pos[piece]) - 1:
            block_rotation_state = block_rotation_state + 1 - len(d_piece_to_pos[piece])
        else:
            block_rotation_state += 1
        return (top, block_rotation_state)
    elif action == 'turnright':
        if block_rotation_state - 1 < 0:
            block_rotation_state = block_rotation_state - 1 + len(d_piece_to_pos[piece])
        else:
            block_rotation_state -= 1
        return (top, block_rotation_state)
    else:
        print 'get_action_top_rotate_state error'

def check_move_legal(field, top_point, block_rotation_state, action, piece):
    top, state = get_action_top_rotate_state(top_point, block_rotation_state, action, piece)
    return check_block_legal(field, top, state, piece)

def check_block_legal(field, top_point, block_rotation_state, piece):
    top = (top_point[1], top_point[0])
    return score_check_legal_new_state(field, top, piece, block_rotation_state)
    """
    block_area = d_piece_to_pos[piece][block_rotation_state]
    (top_x, top_y) = top_point
    if check_goal(top_point, block_rotation_state, piece):
        return True
    if (top_x + len(block_area[0])) > 9 or (top_y + len(block_area)) > 19 or top_x < 0 or top_y < -1:
        return False
    for x in xrange(len(block_area[0])):
        for y in xrange(len(block_area)):
            if block_area[y][x] and field[top_y+y][top_x+x]:
                return False
    return True
    """
# Backtrace ends


# Score
# Reference: https://codemyroad.wordpress.com/2013/04/14/tetris-ai-the-near-perfect-player/
# TODO: Clear the init block's value
'''
    Parameters
    a * AggregateHeights
    b * CompleteLine
    c * Holes
    d * Bumpiness
    t * T
'''
'''
a = -.610066
b = .660666
c = -.75663
d = -.284483
t = 1.326
'''
a = -.510066
b = .760666
c = -6.5663
d = -.184483
t = 1.326

'''
a = -.510066
b = .600666
c = -.45663
d = -.104483
t = 1.126
'''
'''
    Rules
'''

fieldWidth = 10
fieldHeight = 20
blockValue = 1
emptyValue = 0
completeline = fieldWidth * blockValue

def scoreField(field, fake):
    field[0][3], field[0][4], field[0][5], field[0][6] = 0, 0, 0, 0
    CompleteLine = calculateFullLine(field) - fake
    AggregateHeights, Holes, T = calculateHeightAndHolesAndT(field)
    Bumpiness = calculateBumpiness(AggregateHeights)
    score =  a * sum(AggregateHeights) + b * CompleteLine + c * Holes + d * Bumpiness + t * T
    return score

def calculateFullLine(field):
    result = 0
    for line in field:
        if sum(line) == completeline:
            result += 1
    # Scale
    return result

def calculateHeightAndHolesAndT(field):
    heights = [0] * fieldWidth
    numberOfHoles = 0
    numberOfT = 0
    for x in xrange(fieldWidth):
        for y in xrange(fieldHeight):
            if field[y][x] == blockValue:
                if heights[x] < fieldHeight - y:
                    heights[x] = fieldHeight - y
                    if fieldHeight - y == 19:
                        heights[x] = 25
            else:
                # Warning: The order of or's literals is IMPORTANT!
                if x != 0 and x != fieldWidth - 1 and y != 0 and y != fieldHeight - 1 and \
                        (field[y][x - 1] == emptyValue) and (field[y][x + 1] == emptyValue) and (field[y-1][x] == emptyValue) and \
                        (field[y+1][x] == emptyValue) and (bool(field[y-1][x-1] == blockValue) ^ bool(field[y-1][x+1] == blockValue)) and \
                        (field[y+1][x-1] == blockValue) and (field[y+1][x+1] == blockValue):
                    numberOfT += checkTexists(x, y, field)
                    '''
                    T spin ex.
                    0 0 0 0 0 0 1 1 0 0
                    1 1 1 1 0 0 0 1 1 1
                    1 1 1 1 1 0 1 1 1 1
                    1 1 1 1 1 1 1 1 1 1
                    '''
                elif (heights[x] > y):
                    if checkHoles(x, y, field):
                        numberOfHoles += 1
    return heights, numberOfHoles, numberOfT

def checkTexists(x, y, field):
    totlaTClearBlock = 2 * completeline - 4
    currentBlockNum = 0
    for _x in xrange(fieldWidth):
        if field[y][_x] == blockValue:
            currentBlockNum += 1
        if field[y+1][_x] == blockValue:
            if field[y][_x] != emptyValue:
                return 0
            currentBlockNum += 1
    result = (float(currentBlockNum) / totlaTClearBlock)
    return result


def calculateBumpiness(heights):
    bump = 0
    for index in xrange(len(heights)-1):
        bump += abs(heights[index] - heights[index+1])
    return bump
def checkHoles(x, y, field):
    if field[y][x] != emptyValue:
        return False
    if y > 0 and y < fieldHeight - 1 and x > 0 and x < fieldWidth - 1:
        if field[y][x+1] != emptyValue and field[y][x-1] != emptyValue and field[y+1][x] != emptyValue and field[y-1][x] != emptyValue:
            return True
    if y > 0 and field[y-1][x] != emptyValue:
        if x > 0 and x < 9 and field[y][x-1] != emptyValue and field[y][x+1] != emptyValue:
            return True
        elif x == 0 and field[y][x+1] != emptyValue:
            return True
        elif x == 9 and field[y][x-1] != emptyValue:
            return True
    elif y < fieldHeight and y > 1 and field[y-2][x] != emptyValue:
        if x > 0 and x < 9 and field[y-1][x-1] != emptyValue and field[y-1][x+1] != emptyValue and field[y][x-1] != emptyValue and field[y][x+1] != emptyValue:
            if y == fieldHeight - 1:
                return True
            elif field[y+1][x] != emptyValue:
                return True
        elif x == 0 and field[y-1][x+1] != emptyValue and field[y][x+1] != emptyValue:
            if y == fieldHeight - 1:
                return True
            elif field[y+1][x] != emptyValue:
                return True
        elif x == 9 and field[y-1][x-1] != emptyValue and field[y][x-1] != emptyValue:
            if y == fieldHeight - 1:
                return True
            elif field[y+1][x] != emptyValue :
                return True
    return False

'''
def checkHoles(x, y, field):
    if field[y][x] != emptyValue:
        return False
    if y != 0 and y != fieldHeight - 1 and x != 0 and x != fieldWidth - 1:
        if field[y-1][x] != emptyValue and field[y+1][x] != emptyValue and field[y][x-1] != emptyValue and field[y][x+1] != emptyValue:
            return True
    if y == fieldHeight - 1:
        if x == 0:
            if field[y][x+1] != emptyValue and field[y-1][x] != emptyValue:
                return True
        elif x == fieldWidth - 1:
            if field[y][x-1] != emptyValue and field[y-1][x] != emptyValue:
                return True
        else:
            if field[y-1][x] != emptyValue and field[y][x-1] != emptyValue and field[y][x+1] != emptyValue:
                return True
    elif y > 0:
        if x == 0:
            if field[y-1][x] != emptyValue and field[y+1][x] != emptyValue and field[y][x+1] != emptyValue:
                return True
        elif x == fieldWidth - 1:
            if field[y-1][x] != emptyValue and field[y+1][x] != emptyValue and field[y][x-1] != emptyValue:
                return True
    if y > 0 and field[y-1][x] != emptyValue:
        if x > 0 and x < 9 and field[y][x-1] != emptyValue and field[y][x+1] != emptyValue:
            return True
        elif x == 0 and field[y][x+1] != emptyValue:
            return True
        elif x == 9 and field[y][x-1] != emptyValue:
            return True
    elif y < fieldHeight and y > 1 and field[y-2][x] != emptyValue:
        if x > 0 and x < 9 and field[y-1][x-1] != emptyValue and field[y-1][x+1] != emptyValue and field[y][x-1] != emptyValue and field[y][x+1] != emptyValue:
            if y == fieldHeight - 1:
                return True
            elif field[y+1][x] != emptyValue:
                return True
        elif x == 0 and field[y-1][x+1] != emptyValue and field[y][x+1] != emptyValue:
            if y == fieldHeight - 1:
                return True
            elif field[y+1][x] != emptyValue:
                return True
        elif x == 9 and field[y-1][x-1] != emptyValue and field[y][x-1] != emptyValue:
            if y == fieldHeight - 1:
                return True
            elif field[y+1][x] != emptyValue :
                return True
    return False
'''
# Score ends

def find_col_top_and_available_hole(s,width, height):
    col_topRow = []
    col_holeRow = []
    find_peek = False
    peekRow = 19
    
    for row in range(height):
        if 1 in s[row]:
            peekRow = row
            break
    
    for col in range(width):
        find_top = False
        hole_list = []
        for row in range(peekRow, height):
            if not find_top:
                if s[row][col] == 1:
                    find_top = True
                    col_topRow.append(row)
                elif row == height-1:
                    col_topRow.append(height)
            else:
                if s[row][col] == 0:
                    if col == 0 or col == 1:
                        if ( s[row][col+1] == 0 and s[row][col+2] == 0):
                            hole_list.append(row)
                    elif col == width-1 or col == width-2:
                        if ( s[row][col-1] == 0 and s[row][col-2] == 0):
                            hole_list.append(row)
                    else:  
                        if ( s[row][col+1] == 0 and s[row][col+2] == 0) or ( s[row][col-1] == 0 and s[row][col-2] == 0):
                            hole_list.append(row)
        col_holeRow.append(hole_list)
    return col_topRow, col_holeRow, peekRow

def find_available_place(s, piece, width, height, col_topRow, fake):
    
    place_dir_and_score = []
    direction = d_piece_to_direction[piece]
    size = d_piece_size[piece]
    arr_bottom_height = d_piece_to_BtmHeig[piece]
    arr_LR = d_piece_to_LR[piece]
    
    
    for dir in range(direction): #rotation direction of piece
        bottom_height = arr_bottom_height[dir]
        L = arr_LR[dir][0]
        R = arr_LR[dir][1]
        for target_x in range(0-L, width - size + (size-1 - R) + 1): #from the game board left to the right
            # put on top of coloum
            min = height
            touch_x = width
            for x in range(size): #which column will touch the brick first
                if bottom_height[x] == -1: continue
                diff = col_topRow[target_x + x] - bottom_height[x]
                if diff < min:
                    min = diff
                    touch_x = x
            target_y = col_topRow[target_x + touch_x] - (bottom_height[touch_x] + 1)
            place = (target_y, target_x)
                            
            is_legal, score = check_legal_new_state(s,place,piece, dir,0, fake)
            if is_legal:
                place_dir_and_score.append([place, dir, score])
            
            # put to stuff the hole
            #if target_x == 6 and dir == 3: print range( target_y+ 1, height - (max(bottom_height) + 1)+1)
            for stuff_y in range( target_y+ 1, height - (max(bottom_height) + 1) + 1):
                place = (stuff_y, target_x)
                is_legal, score = check_legal_new_state(s, place, piece, dir, 1, fake)
                if is_legal:
                    place_dir_and_score.append([place, dir, score])                 
    return place_dir_and_score

##############
def find_available_place_return_field(s, piece, width, height, col_topRow, fake):
    
    place_dir_and_score = []
    direction = d_piece_to_direction[piece]
    size = d_piece_size[piece]
    arr_bottom_height = d_piece_to_BtmHeig[piece]
    arr_LR = d_piece_to_LR[piece]
    
    
    for dir in range(direction): #rotation direction of piece
        bottom_height = arr_bottom_height[dir]
        L = arr_LR[dir][0]
        R = arr_LR[dir][1]
        for target_x in range(0-L, width - size + (size-1 - R) + 1): #from the game board left to the right
            # put on top of coloum
            min = height
            touch_x = width
            for x in range(size): #which column will touch the brick first
                if bottom_height[x] == -1: continue
                diff = col_topRow[target_x + x] - bottom_height[x]
                if diff < min:
                    min = diff
                    touch_x = x
            target_y = col_topRow[target_x + touch_x] - (bottom_height[touch_x] + 1)
            place = (target_y, target_x)
                            
            is_legal, new_score , new_field = check_legal_new_state_return_field(s,place,piece, dir,0, fake)
            if is_legal:
                place_dir_and_score.append([place, dir, new_score, new_field])
            
            # put to stuff the hole
            #if target_x == 6 and dir == 3: print range( target_y+ 1, height - (max(bottom_height) + 1)+1)
            for stuff_y in range( target_y+ 1, height - (max(bottom_height) + 1) + 1):
                place = (stuff_y, target_x)
                is_legal, new_score, new_field = check_legal_new_state_return_field(s, place, piece, dir, 1, fake)
                if is_legal:
                    place_dir_and_score.append([place, dir,new_score, new_field])                 
    return place_dir_and_score

def check_legal_new_state_return_field(s, pos, piece, d, is_stuff, fake):
    y = pos[0]
    x = pos[1]
    new_s = [l[:] for l in s]
    arr_size = d_piece_size[piece]
    shape = d_piece_to_pos[piece][d]
    bottom_height = d_piece_to_BtmHeig[piece][d]
    for row in range(arr_size):
        for col in range(arr_size):
            if shape[row][col] == 0: continue
            #print y, row, x, col
            if y+row >= 20 or x+col >= 10 or y+row < 0 or x+col < 0:
                return False, -9999 , 0
            if s[y+row][x+col] == 1 and shape[row][col] == 1:
                return False,-9999, 0
            elif s[y+row][x+col] == 0 and shape[row][col] == 1:
                new_s[y+row][x+col] = 1
    is_float = True
    if is_stuff:
        for col in range(arr_size):
            if bottom_height[col] == -1: continue
            #if x == 6 and y == 17: print y+bottom_height[col]+1, bottom_height
            if y+bottom_height[col]+1 == 20:
                is_float = False
            elif s[y+bottom_height[col]+1][x+col] == 1:
                is_float = False
        if is_float:
            return False,-9999, 0
    score = scoreField(new_s, fake)
    return True,  score, new_s
###################           
def check_legal_new_state(s, pos, piece, d, is_stuff, fake):
    y = pos[0]
    x = pos[1]
    new_s = [l[:] for l in s]
    arr_size = d_piece_size[piece]
    shape = d_piece_to_pos[piece][d]
    bottom_height = d_piece_to_BtmHeig[piece][d]
    for row in range(arr_size):
        for col in range(arr_size):
            if shape[row][col] == 0: continue
            #print y, row, x, col
            if y+row >= 20 or x+col >= 10 or y+row < 0 or x+col < 0:
                return False, -9999 
            if s[y+row][x+col] == 1 and shape[row][col] == 1:
                return False,-9999
            elif s[y+row][x+col] == 0 and shape[row][col] == 1:
                new_s[y+row][x+col] = 1
    is_float = True
    if is_stuff:
        for col in range(arr_size):
            if bottom_height[col] == -1: continue
            #if x == 6 and y == 17: print y+bottom_height[col]+1, bottom_height
            if y+bottom_height[col]+1 == 20:
                is_float = False
            elif s[y+bottom_height[col]+1][x+col] == 1:
                is_float = False
        if is_float:
            return False,-9999
        
    score = scoreField(new_s, fake)
    return True, score
            
def score_check_legal_new_state(s, pos, piece, d):
    y = pos[0]
    x = pos[1]
    arr_size = d_piece_size[piece]
    shape = d_piece_to_pos[piece][d]
    bottom_height = d_piece_to_BtmHeig[piece][d]
    for row in range(arr_size):
        for col in range(arr_size):
            if check_goal((x,y), d, piece): return True
            if shape[row][col] == 0: continue
            #print y, row, x, col
            if y+row >= 20 or x+col >= 10 or y+row < 0 or x+col < 0:
                return False
            if s[y+row][x+col] == 1 and shape[row][col] == 1:
                return False
    return True
