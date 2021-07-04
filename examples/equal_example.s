entry:
	mov 1, rans
	mov rans, [rsp + 1]
	mov 0, rans
	mov rans, [rsp + 2]
	mov 0, rans
	cmp [rsp + 2], rans
	jne not_equal__4
equal__3:
	mov 1, rans
	jmp end__5
not_equal__4:
	mov 0, rans
end__5:
	cmp [rsp + 1], rans
	jne not_equal__1
equal__0:
	mov 1, rans
	jmp end__2
not_equal__1:
	mov 0, rans
end__2:
