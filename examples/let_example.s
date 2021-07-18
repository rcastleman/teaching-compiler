entry:
	mov 5, rans
	mov rans, [rsp + 1]
	mov 2, rans
	mov rans, [rsp + 2]
	mov 9, rans
	mov rans, [rsp + 3]
	mov 1, rans
	mov rans, [rsp + 4]
	mov 2, rans
	add [rsp + 4], rans
