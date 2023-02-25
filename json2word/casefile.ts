import { CaseFile } from "./models/casefilesModel";
import {
	dateToString,
	makeTextBody,
	makeFrontMatter,
	makeSpace,
	makeImageBody,
} from "./common";

import { Document, Packer } from "docx";
import { makeTwoColumnsRow } from "./table";
import { linkTextParagraph, quickTextParagraph } from "./text";

const casefiles: CaseFile[] = require("../data/casefiles.json");
const fs = require("fs");

export function casefileFrontMatter(casefile: CaseFile) {
	const title = makeTwoColumnsRow("标题", [
		quickTextParagraph(casefile.title),
	]);
	const abstract = makeTwoColumnsRow("摘要", [
		quickTextParagraph(casefile.description),
	]);
	const header = makeTwoColumnsRow("头文件", [
		quickTextParagraph(casefile.header),
	]);
	const url = makeTwoColumnsRow("链接", [
		quickTextParagraph(casefile.slug.current),
	]);
	const order = makeTwoColumnsRow("顺序", [
		quickTextParagraph(String(casefile.order)),
	]);
	const cover = makeTwoColumnsRow("配图链接", [
		quickTextParagraph(casefile.mainImageUrl),
	]);
	const featured = makeTwoColumnsRow("置顶", [
		quickTextParagraph(String(casefile.featured)),
	]);
	const tags = makeTwoColumnsRow("标签", [
		quickTextParagraph(casefile.tags ? casefile.tags.join("，") : ""),
	]);
	const category = makeTwoColumnsRow("类别", [
		quickTextParagraph(casefile.classification),
	]);
	const publish = makeTwoColumnsRow("发布时间", [
		quickTextParagraph(dateToString(casefile.publishedAt)),
	]);
	const written = makeTwoColumnsRow("收录时间", [
		quickTextParagraph(dateToString(casefile.writtenAt)),
	]);
	const related = makeTwoColumnsRow(
		"扩展阅读",
		casefile.related
			? casefile.related.map((relate) => {
					return linkTextParagraph(relate.title, relate.urlField);
			  })
			: makeSpace(0)
	);
	return [
		title,
		abstract,
		header,
		url,
		order,
		cover,
		featured,
		tags,
		category,
		publish,
		written,
		related,
	];
}

const run = async () => {
	for (const casefile of casefiles) {
		const table = makeFrontMatter(casefile, casefileFrontMatter);
		const body = await makeTextBody(casefile.body);
		const images = makeImageBody(
			casefile,
			(casefile) => `./images/casefile/${casefile.title}`,
			300
		);
		const doc = new Document({
			sections: [
				{
					properties: {},
					children: [table, ...makeSpace(2), ...body, ...images],
				},
			],
		});

		Packer.toBuffer(doc).then((buffer) => {
			fs.writeFileSync(
				`mswords/casefile/${casefile.order}_${casefile.title}.docx`,
				buffer
			);
		});
	}
};

run();
