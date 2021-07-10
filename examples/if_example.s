entry:
	mov 1, rans
	mov rans, [rsp + 1]
	mov 2, rans
	cmp [rsp + 1], rans
	jne not_equal__4
equal__3:
	mov 1, rans
	jmp equal_end__5
not_equal__4:
	mov 0, rans
equal_end__5:
	cmp rans, 0
	je if_cond_false__0
if_cond_true__1:
	mov 13, rans
	jmp if_is_done__2
if_cond_false__0:
	mov 19, rans
if_is_done__2:
