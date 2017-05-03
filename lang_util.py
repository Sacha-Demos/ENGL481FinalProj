

def print_grid(grid):
    for row in grid:
        print(row)

def weight_func(x):
    return 1. / (1+x)
        
def edit_distance(seqone, seqtwo, similarities = {}, final_ign = {}, weight_func = None):
    if seqone == seqtwo:
        return 0.
    n = len(seqone) + 1
    m = len(seqtwo) + 1
    grid = [[0. for j in range(m)] for i in range(n)]
    for i in range(n):
        grid[i][0] = float(i)
    for j in range(m):
        grid[0][j] = float(j)
    for i in range(1,n):
        for j in range(1,m):
            diff = 1.
            edit = diff
            tokone = seqone[i-1]
            toktwo = seqtwo[j-1]
            if tokone == toktwo:
                diff = 0.
                edit = 0.
            elif (tokone, toktwo) in similarities:
                edit = similarities[(tokone, toktwo)]
            elif (toktwo, tokone) in similarities:
                edit = similarities[(toktwo, tokone)]

            if weight_func:
                weight = weight_func(min(n-i-1, m-j-1))
                edit *= weight
                diff *= weight
                
            grid[i][j] = min(grid[i-1][j-1]+edit, grid[i][j-1]+diff, grid[i-1][j]+diff)
    values = [grid[n-1][m-1]]
    if seqtwo[-1] in final_ign:
        values.append(grid[n-1][m-2] + (weight_func(0)*final_ign[seqtwo[-1]]))
    if seqone[-1] in final_ign:
        values.append(grid[n-2][m-1]+ (weight_func(0)*final_ign[seqone[-1]]))
    return min(values)

def similarity_score(seqone, seqtwo, similarities = {}, finals = {}, weight_func = None, power = 1):
    editd = edit_distance(seqone, seqtwo, similarities, finals, weight_func)
    if weight_func:
        worst = sum([weight_func(x) for x in range(max(len(seqone),len(seqtwo)))])
    else:
        worst = max(len(seqone), len(seqtwo))
    ratio = max(1 - (editd / worst), 0)
    if power != 1:
        ratio = pow(ratio, power)
    return ratio

if __name__ == "__main__":
    print(similarity_score("one","pone", power=4))
