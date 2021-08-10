function_fact_3410109347314543000:
	mov [rsp + 1], rans
	mov rans, [rsp + 2]
	mov 0, rans
	cmp [rsp + 2], rans
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
	mov 1, rans
	jmp if_is_done__2
if_cond_false__0:
	mov [rsp + 1], rans
	mov rans, [rsp + 2]
	mov [rsp + 1], rans
	sub 1, rans
	mov rans, [rsp + 4]
	add 2, rsp
	call function_fact_3410109347314543000
	sub 2, rsp
	mul [rsp + 2], rans
if_is_done__2:
	ret
entry:
	mov 5, rans
	mov rans, [rsp + 2]
	add 0, rsp
	call function_fact_3410109347314543000
	sub 0, rsp
	print rans
