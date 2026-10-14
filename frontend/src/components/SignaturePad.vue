<template>
	<div class="space-y-1">
		<canvas
			ref="cv"
			class="w-full h-32 rounded-xl border border-dashed border-slate-300 bg-white touch-none"
			@pointerdown="start"
			@pointermove="move"
			@pointerup="end"
			@pointerleave="end"
		></canvas>
		<button type="button" @click="clear" class="text-[11px] font-semibold text-slate-500 underline">Clear signature</button>
	</div>
</template>

<script setup>
import { ref, onMounted } from "vue"

const model = defineModel() // PNG data URL, or null when empty
const cv = ref(null)
let ctx = null
let drawing = false

onMounted(() => {
	const c = cv.value
	c.width = c.clientWidth
	c.height = c.clientHeight
	ctx = c.getContext("2d")
	ctx.lineWidth = 2.2
	ctx.lineCap = "round"
	ctx.strokeStyle = "#0f172a"
})

const pos = (e) => {
	const r = cv.value.getBoundingClientRect()
	return [e.clientX - r.left, e.clientY - r.top]
}
function start(e) {
	drawing = true
	const [x, y] = pos(e)
	ctx.beginPath()
	ctx.moveTo(x, y)
}
function move(e) {
	if (!drawing) return
	const [x, y] = pos(e)
	ctx.lineTo(x, y)
	ctx.stroke()
}
function end() {
	if (!drawing) return
	drawing = false
	model.value = cv.value.toDataURL("image/png")
}
function clear() {
	ctx.clearRect(0, 0, cv.value.width, cv.value.height)
	model.value = null
}
</script>