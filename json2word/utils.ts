import { HeadingLevel } from "docx";
import { Body } from "./models/postModel";

export const styleMapping = new Map<number, HeadingLevel>();
for (const [index, value] of Object.values(HeadingLevel).entries()) {
	styleMapping.set(index, value);
}

export function inferRelativeHeadingMap(bodies: Body[]) {
	const styles: Number[] = [];
	for (const body of bodies) {
		if (body.style.startsWith("h")) {
			styles.push(Number(body.style.slice(1)));
		}
	}
	let style_num = [...new Set(styles)].sort();

	const style_map = new Map<string, HeadingLevel>();
	for (const [index, style] of style_num.entries()) {
		style_map.set(`h${style}`, styleMapping.get(index) as HeadingLevel);
	}
	return style_map;
}

export function inferParagraphSpacing(para_style: {
	style?: string;
	heading?: HeadingLevel;
}) {
	let spacing = 150;
	if (!para_style.heading) {
		return spacing;
	} else {
		for (const [index, value] of Object.values(HeadingLevel).entries()) {
			if (value == para_style.heading) {
				return 300 - index * 30;
			}
		}
	}
}
