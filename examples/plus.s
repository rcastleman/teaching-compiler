entry:
	mov 10, rans
	mov rans, [rsp + 1]
	mov 1, rans
	mov rans, [rsp + 2]
	mov 1, rans
	add [rsp + 2], rans
	add [rsp + 1], rans
