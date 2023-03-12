import { HeadingLevel } from "docx";
import { Body, Child, MarkDef, Reference } from "./models/base";
import * as path from "node:path";
import { DocType, FootnoteType } from "./render/core";
import { Article } from "./models/article";
import { Casefile } from "./models/casefile";

export const styleMapping = new Map<number, HeadingLevel>();
for (const [index, value] of Object.values(HeadingLevel).entries()) {
	styleMapping.set(index, value);
}

export function isImageRun(child: Child, mark_defs: MarkDef[]) {
	for (const mark of child.marks) {
		let mark_type = mark_defs.filter((mark_def) => mark_def._key == mark);
		if (mark_type.length == 0) {
			return false;
		} else {
			let m = mark_type[0];
			if (m._type == "imagelink") {
				return true;
			}
		}
	}
	return false;
}

export function makeParagraphStyle(
	style: string,
	style_map: Map<string, HeadingLevel>
) {
	if (style.startsWith("h")) {
		return { heading: style_map.get(style) };
	} else if (style == "blockquote") {
		return { bullet: { level: 0 } };
	} else {
		return { style: "Normal" };
	}
}

export function getMarkTypeByKey(mark: string, mark_defs: MarkDef[]) {
	const type = mark_defs.filter((mark_def) => mark_def._key == mark)[0];
	return type;
}

export function getMarkTypeByType(mark: string, mark_defs: MarkDef[]) {
	const type = mark_defs.filter((mark_def) => mark_def._type == mark)[0];
	return type;
}

export const sleep = (s: number) => new Promise((r) => setTimeout(r, s * 1000));

export function urlize(href: string, basename: string) {
	if (href.startsWith("http")) {
		return new URL(href);
	}

	let url = new URL(path.join(basename, path.normalize(String.raw`${href}`)));

	return url;
}

export function transformSize(height: any, width: any, size: number = 100) {
	let ratio = height / width;
	return [size, size * ratio];
}

export function getImageExt(name: string) {
	let ext = name.split(".").pop();
	if (ext) {
		if (["jpeg", "jpg", "png", "gif"].includes(ext)) {
			return ext;
		}
	}
	return "jpg";
}

export function inferRelativeHeadingMap(bodies: Body[]) {
	const styles: Number[] = [];
	for (const body of bodies) {
		if (body.style!.startsWith("h")) {
			styles.push(Number(body.style!.slice(1)));
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

export function inferFootnotes(doc: DocType) {
	doc = doc as Casefile | Article;
	const footnotes: Reference[] = [];
	for (const paragraph of doc.body!) {
		for (const markDef of paragraph.markDefs) {
			if (markDef.reference && markDef.reference.length != 0) {
				for (const ref of markDef.reference) {
					footnotes.push(ref);
				}
			}
		}
	}
	return footnotes;
}
