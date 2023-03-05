import { Table, Paragraph, TableRow, WidthType } from "docx";
import { Casefile } from "./models/casefile";
import { Body } from "./models/base";
import { Article } from "./models/article";
import { Timeline } from "./models/timeline";
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
	data: Casefile | Article | Timeline,
	fn: (data: any) => TableRow[]
) {
	const table = new Table({
		rows: [...fn(data)],
		width: { size: 100, type: WidthType.PERCENTAGE },
	});
	return table;
}

export function makeImageBody(
	data: Timeline | Casefile,
	nameRule: (data: any) => string,
	size: number = 100
) {
	let savePath = nameRule(data);
	let paragraphs: Paragraph[] = [];
	if (data.imageUrls) {
		for (let index = 0; index < data.imageUrls!.length; index++) {
			let filename = `${savePath}_${index}.jpg`;
			paragraphs.push(
				makeImageParagraph(
					filename,
					size,
					data.imageUrls[index].urlField
				)
			);
		}
	}
	return paragraphs;
}
