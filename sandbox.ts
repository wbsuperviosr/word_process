import { ExternalHyperlink, Packer, ImageRun, Paragraph, Document } from "docx";
import fetch from "cross-fetch";
import * as fs from "fs";
import sizeOf from "image-size";

const url =
	"https://images.pexels.com/photos/7303979/pexels-photo-7303979.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1";

const dowloandImg = async (link: string) => {
	const response = await fetch(link);
	const arrayBuffer = await response.arrayBuffer();
	const buffer = Buffer.from(arrayBuffer);
	return buffer;
};

async function main() {
	const buffer = await dowloandImg(url);
	let dims = sizeOf(buffer);
	console.log(dims);

	let image = new ImageRun({
		data: buffer,
		transformation: {
			height: dims.height! * 0.5,
			width: dims.width! * 0.5,
		},
		altText: {
			name: "this is the name",
			description: "this is the description",
			title: "this is the title",
		},
	});

	const doc = new Document({
		sections: [
			{
				properties: {},
				children: [new Paragraph({ children: [image] })],
			},
		],
	});

	Packer.toBuffer(doc).then((buffer) => {
		fs.writeFileSync(`test.docx`, buffer);
	});
}
main();
