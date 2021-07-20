entry:
	mov 5, rans
	mov rans, [rsp + 1]
	mov 20, rans
	mov rans, [rsp + 2]
	mov 9, rans
	mov rans, [rsp + 3]
	mov [rsp + 3], rans
	mov rans, [rsp + 4]
	mov [rsp + 1], rans
	mov rans, [rsp + 5]
	mov [rsp + 2], rans
	add [rsp + 5], rans
	add [rsp + 4], rans
	print rans
