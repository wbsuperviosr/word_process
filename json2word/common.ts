import { Table, Paragraph, TableRow, WidthType } from "docx";
import { CaseFile } from "./models/casefilesModel";
import { Post, Body } from "./models/postModel";
import { Timeline } from "./models/timelineModel";
import { inferRelativeHeadingMap } from "./utils";
import { makeImageParagraph } from "./image";
import { makeTextBodyParagraph } from "./text";

export async function makeTextBody(
	bodies: Body[],
	image_dir: string = "",
	image_name: string = "",
	font_family = "Microsoft YaHei"
) {
	let paragraphs: Paragraph[] = [];
	const style_map = inferRelativeHeadingMap(bodies);
	for (const body of bodies) {
		paragraphs.push(
			await makeTextBodyParagraph(
				body,
				style_map,
				image_dir,
				image_name,
				font_family
			)
		);
	}
	return paragraphs;
}

export function makeSpace(number: number) {
	let paragraphs: Paragraph[] = [];
	for (let index = 0; index < number; index++) {
		const element = new Paragraph("");
		paragraphs.push(element);
	}
	return paragraphs;
}

export function dateToString(date: Date | string) {
	let d: Date = new Date();
	if (typeof date === "string" || date instanceof String) {
		// d = new Date(date as string);
		d.setTime(Date.parse(date as string));
	} else {
		d = date as Date;
	}
	return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日`;
}

export function makeFrontMatter(
	data: CaseFile | Post | Timeline,
	fn: (data: any) => TableRow[]
) {
	const table = new Table({
		rows: [...fn(data)],
		width: { size: 100, type: WidthType.PERCENTAGE },
	});
	return table;
}

export function makeImageBody(
	data: Timeline | CaseFile,
	nameRule: (data: any) => string,
	size: number = 100
) {
	let savePath = nameRule(data);
	let paragraphs: Paragraph[] = [];
	if (data.image_urls) {
		for (let index = 0; index < data.image_urls.length; index++) {
			let filename = `${savePath}_${index}.jpg`;
			paragraphs.push(
				makeImageParagraph(
					filename,
					size,
					data.image_urls[index].urlField
				)
			);
		}
	}
	return paragraphs;
}
