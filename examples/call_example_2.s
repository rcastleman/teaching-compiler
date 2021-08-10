entry:
	mov 1, rans
	mov rans, [rsp + 2]
	mov 3, rans
	mov rans, [rsp + 3]
	mov 2, rans
	mov rans, [rsp + 4]
	mov 2, rans
	add [rsp + 4], rans
	add [rsp + 3], rans
	mov rans, [rsp + 3]
	add 0, rsp
	call function_frog_9215499036358607972
	sub 0, rsp
	print rans
