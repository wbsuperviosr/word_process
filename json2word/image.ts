import sizeOf from "image-size";
import { ExternalHyperlink, ImageRun, Paragraph } from "docx";

// const fs = require("fs");
import * as fs from "fs";

export function transformSize(height: any, width: any, size: number = 100) {
	let ratio = height / width;
	return [size, size * ratio];
}

export function makeImageParagraph(
	savePath: string,
	size: number = 100,
	link: string = ""
) {
	let dims = sizeOf(savePath);
	const [width, height] = transformSize(dims.height, dims.width, size);
	const buffer = fs.readFileSync(savePath);
	let image = new ImageRun({
		data: buffer,
		transformation: {
			height: height,
			width: width,
		},
	});
	if (link.startsWith("http")) {
		let image_link = new ExternalHyperlink({
			children: [image],
			link: link,
		});
		return new Paragraph({ children: [image_link] });
	} else {
		return new Paragraph({ children: [image] });
	}
}
