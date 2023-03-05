import {
	AlignmentType,
	ExternalHyperlink,
	HeadingLevel,
	HorizontalPositionAlign,
	ImageRun,
	LineRuleType,
	Paragraph,
	TextRun,
	TextWrappingSide,
	TextWrappingType,
	UnderlineType,
	VerticalPositionAlign,
	HorizontalPositionRelativeFrom,
	VerticalPositionRelativeFrom,
	FootnoteReferenceRun,
} from "docx";
import { downloadImage } from "./imageio/download";
import { Child, Body, MarkDef } from "./models/base";
import { transformSize } from "./image";
import { inferParagraphSpacing } from "./utils";
import sizeOf from "image-size";

const fs = require("fs");

export function quickTextParagraph(
	text?: string,
	fontFamily: string = "Microsoft YaHei",
	fontSize: number = 20
) {
	return new Paragraph({
		children: [
			new TextRun({
				text: text ? text : "",
				font: fontFamily,
				size: fontSize,
			}),
		],
	});
}

export function linkTextParagraph(
	text: string,
	link: string,
	fontFamily: string = "Microsoft YaHei",
	fontSize: number = 20
) {
	let hyperlink = link.startsWith("http")
		? link
		: `https://liuxin.express/${link}`;
	const paragraph = new Paragraph({
		children: [
			new ExternalHyperlink({
				children: [
					new TextRun({
						text: text,
						style: "Hyperlink",
						font: fontFamily,
						size: fontSize,
					}),
				],
				link: hyperlink,
			}),
		],
	});
	return paragraph;
}

function getMarkType(mark: string, mark_defs: MarkDef[]) {
	const type = mark_defs.filter((mark_def) => mark_def._key == mark)[0];
	return type;
}

function makeParagraphStyle(
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

function isImageRun(child: Child, mark_defs: MarkDef[]) {
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

async function makeTextBodyParagraphRun(
	child: Child,
	mark_defs: MarkDef[],
	image_dir: string = "",
	image_name: string = "",
	font_family = "Microsoft YaHei"
) {
	if (isImageRun(child, mark_defs)) {
		let mark_def = mark_defs.filter(
			(mark_def) => mark_def._type == "imagelink"
		)[0];
		await downloadImage(
			image_dir,
			`${image_name}_${mark_def._key}.jpg`,
			mark_def.href!
		);

		let savePath = `${image_dir}/${image_name}_${mark_def._key}.jpg`;
		let dims = sizeOf(savePath);
		const [width, height] = transformSize(dims.height, dims.width, 300);
		let run = new ImageRun({
			data: fs.readFileSync(savePath),
			transformation: {
				height: height,
				width: width,
			},
			floating: {
				horizontalPosition: {
					relative: HorizontalPositionRelativeFrom.PAGE,
					align: HorizontalPositionAlign.CENTER,
				},
				verticalPosition: {
					relative: VerticalPositionRelativeFrom.PARAGRAPH,
					align: VerticalPositionAlign.CENTER,
				},
				lockAnchor: true,
				wrap: {
					type: TextWrappingType.TOP_AND_BOTTOM,
					side: TextWrappingSide.BOTH_SIDES,
				},
			},
		});
		if (mark_def.href!.startsWith("http")) {
			return [
				new ExternalHyperlink({
					children: [run],
					link: mark_def.href!,
				}),
			];
		}
		return [run];
	} else {
		let style = {
			text: child.text,
			font: font_family,
			size: 22,
		};

		let hyperlink: string = "";
		for (const mark of child.marks) {
			if (mark == "strong") {
				Object.assign(style, { bold: true });
			} else if (mark == "em") {
				Object.assign(style, { italics: true });
			} else if (mark == "u") {
				Object.assign(style, {
					underline: { type: UnderlineType.SINGLE },
				});
			} else {
				let mark_type = getMarkType(mark, mark_defs);
				switch (mark_type._type) {
					case "link":
						Object.assign(style, { style: "Hyperlink" });
						hyperlink = mark_type.href!.startsWith("http")
							? mark_type.href!
							: `https://liuxin.express${mark_type.href}`;
						break;

					default:
						break;
				}
			}
		}
		if (hyperlink == "") {
			return [new TextRun(style)];
		} else {
			return [
				new ExternalHyperlink({
					children: [new TextRun(style)],
					link: hyperlink,
				}),
			];
		}
	}
}

export async function makeTextBodyParagraph(
	body: Body,
	style_map: Map<string, HeadingLevel>,
	image_dir: string = "",
	image_name: string = "",
	font_family = "Microsoft YaHei"
) {
	let runs: any[] = [];
	for (const child of body.children) {
		runs.push(
			...(await makeTextBodyParagraphRun(
				child,
				body.markDefs,
				image_dir,
				image_name,
				font_family
			))
		);
	}

	const para_style = makeParagraphStyle(body.style!, style_map);
	const spacing = inferParagraphSpacing(para_style);
	const paragraph = new Paragraph({
		children: runs,
		...para_style,
		alignment: AlignmentType.JUSTIFIED,
		spacing: {
			after: spacing,
			before: spacing,
			line: 300,
			lineRule: LineRuleType.EXACT,
		},
	});
	return paragraph;
}
