import { Author, Post } from "./models/postModel";
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

const posts: Post[] = require("../data/voices.json");
const authors: Author[] = require("../data/authors.json");
const post = posts.filter(
	(post) => post.slug.current == "what_do_liuxin_supporters_think1"
)[0];

const fs = require("fs");

function authorName(key: string) {
	return authors.filter((author) => author._id == key)[0].name;
}

export function postFrontMatter(post: Post) {
	const title = makeTwoColumnsRow("标题", [quickTextParagraph(post.title)]);

	const author = makeTwoColumnsRow("作者", [
		quickTextParagraph(authorName(post.author._ref)),
	]);

	const abstract = makeTwoColumnsRow("摘要", [
		quickTextParagraph(post.description),
	]);

	const url = makeTwoColumnsRow("链接", [
		quickTextParagraph(post.slug.current),
	]);

	const cover = makeTwoColumnsRow("配图链接", [
		quickTextParagraph(post.mainImageUrl),
	]);
	const featured = makeTwoColumnsRow("置顶", [
		quickTextParagraph(String(post.featured)),
	]);
	const tags = makeTwoColumnsRow("标签", [
		quickTextParagraph(post.tags ? post.tags.join("，") : ""),
	]);
	const category = makeTwoColumnsRow("类别", [
		quickTextParagraph(post.category),
	]);
	const publish = makeTwoColumnsRow("发布时间", [
		quickTextParagraph(dateToString(post.publishedAt)),
	]);
	const written = makeTwoColumnsRow("收录时间", [
		quickTextParagraph(dateToString(post.writtenAt)),
	]);
	const related = makeTwoColumnsRow(
		"扩展阅读",
		post.related
			? post.related.map((relate) => {
					return linkTextParagraph(relate.title, relate.urlField);
			  })
			: makeSpace(0)
	);
	return [
		title,
		author,
		abstract,
		url,
		cover,
		featured,
		tags,
		category,
		publish,
		written,
		related,
	];
}

async function main(post: Post) {
	const table = makeFrontMatter(post, postFrontMatter);
	const body = await makeTextBody(post.body, "images/post/", `${post.title}`);

	const doc = new Document({
		sections: [
			{
				properties: {},
				children: [table, ...makeSpace(2), ...body],
			},
		],
	});

	Packer.toBuffer(doc).then((buffer) => {
		fs.writeFileSync(`mswords/post/${post.title}.docx`, buffer);
	});
}

main(post);

// const run = async () => {
// 	for (const post of posts) {
// 		try {
// 			await main(post);
// 		} catch (err: any) {
// 			console.log(post.title, "failed");
// 		}
// 	}
// };

// run();
