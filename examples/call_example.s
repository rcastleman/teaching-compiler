function_frog_4026391880741112109:
	mov [rsp + 1], rans
	mov rans, [rsp + 3]
	mov [rsp + 2], rans
	add [rsp + 3], rans
	ret
entry:
	mov 1, rans
	mov rans, [rsp + 2]
	mov 2, rans
	mov rans, [rsp + 3]
	add 0, rsp
	call function_frog_4026391880741112109
	sub 0, rsp
	print rans
