import {
	AlignmentType,
	Document,
	ExternalHyperlink,
	HeadingLevel,
	HorizontalPositionAlign,
	HorizontalPositionRelativeFrom,
	ImageRun,
	IParagraphOptions,
	IRunOptions,
	LineRuleType,
	Packer,
	Paragraph,
	Table,
	TableCell,
	TableRow,
	TextRun,
	TextWrappingSide,
	TextWrappingType,
	UnderlineType,
	VerticalPositionAlign,
	VerticalPositionRelativeFrom,
	WidthType,
} from "docx";

import {
	inferRelativeHeadingMap,
	inferReference,
	inferParagraphSpacing,
	isImageRun,
	getMarkTypeByKey,
	getMarkTypeByType,
	urlize,
	transformSize,
	getImageExt,
	makeParagraphStyle,
} from "../utils";

import * as fs from "fs";
import * as path from "node:path";
import fetch from "cross-fetch";
import sizeOf from "image-size";
import {
	ArticleUrl,
	Body,
	Child,
	ImageUrl,
	MarkDef,
	Slug,
	FieldStringMap,
} from "../models/base";
import { Service } from "../service";
import { Casefile } from "../models/casefile";
import { Timeline } from "../models/timeline";
import { Article } from "../models/article";
import { Rumor } from "../models/rumor";
import { logger } from "../logger";

export type IDocxConfig = {
	docType: string;
	outputDir: string;
	imageDir: string;
	cacheImage: boolean;
};

type RunType = TextRun | ImageRun | ExternalHyperlink;
type DocType = Casefile | Timeline | Article | Rumor;

import * as enzh from "../../EnZh.json";

const dict = new Map();
for (const [key, value] of Object.entries(enzh)) {
	dict.set(key, value);
}

export abstract class DocxCore {
	fontFamily: string = "Microsoft YaHei";
	fontSize: number = 22;
	imageCount: number = 0;
	imageScale: number = 300;
	baseUri: string = "https://liuxin.express";
	imageUri: string = "https://assets.wbavengers.com";
	_imageName: string = "";

	constructor(public config: IDocxConfig, public service: Service) {
		this.config = config;
		this.service = service;
	}

	abstract get imageInFM(): boolean;
	abstract get bodyInFM(): boolean;

	async renderFontMatter(doc: DocType): Promise<Table> {
		let rows: TableRow[] = [];
		for (const [key, item] of Object.entries(doc)) {
			const literal = this.fieldMap.get(key);
			const ckey = dict.get(key) ? dict.get(key) : key;
			switch (literal) {
				case "string":
					rows.push(
						await this.tableRow(ckey, [this.textParagraph(item)])
					);
					break;
				case "number":
					rows.push(
						await this.tableRow(ckey, [
							this.textParagraph(String(item)),
						])
					);
					break;
				case "boolean":
					rows.push(
						await this.tableRow(ckey, [
							this.textParagraph(String(item)),
						])
					);
					break;
				case "listString":
					rows.push(
						await this.tableRow(ckey, [
							this.textParagraph(item.join(",")),
						])
					);
					break;
				case "slug":
					rows.push(
						await this.tableRow(ckey, [
							this.textParagraph(item.current),
						])
					);
					break;
				case "body":
					if (this.bodyInFM) {
						rows.push(
							await this.tableRow(
								ckey,
								await this.renderBodies(item as Body[])
							)
						);
					}
					break;
				case "listArticleUrl":
					rows.push(
						await this.tableRow(ckey, this.renderArticleUrls(item))
					);
					break;
				case "listImageUrl":
					if (this.imageInFM) {
						rows.push(
							await this.tableRow(
								ckey,
								await this.renderImageUrls(item)
							)
						);
					}
					break;
				case "datetime":
					let date = new Date(item);
					rows.push(
						await this.tableRow(ckey, [
							this.textParagraph(date.toLocaleDateString()),
						])
					);
					break;
				default:
					logger.error(`unknown literal ${key}`);
					throw new Error(`unknown literal ${key}`);
			}
		}
		return new Table({
			rows: rows,
			width: { size: 100, type: WidthType.PERCENTAGE },
		});
	}

	async downloadImage(url: string): Promise<Buffer> {
		const link = urlize(url, this.imageUri);

		if (link.hostname == "assets.wbavengers.com") {
			logger.info(
				`Downloading image ${decodeURI(link.pathname)} from Cloudflare`
			);
			const responseBuffer = await this.service
				.get_cloudflare()
				.getFile(decodeURI(link.pathname.slice(1)));
			return Buffer.from(responseBuffer!);
		} else {
			logger.info(
				`Downloading image ${decodeURI(link.pathname)} from HTTP`
			);
			const response = await fetch(link.href);
			const arrayBuffer = await response.arrayBuffer();
			const buffer = Buffer.from(arrayBuffer);
			return buffer;
		}
	}

	async getImageBuffer(url: string): Promise<Buffer> {
		let imageBuffer: Buffer;

		if (this.config.cacheImage) {
			const ext = getImageExt(url);
			const imageNameIdx = `${this.imageName}_${this.imageCount}.${ext}`;
			const imagePath = path.join(
				this.imageDir(this.imageName),
				imageNameIdx
			);
			if (!fs.existsSync(this.imageDir(this.imageName))) {
				fs.mkdirSync(this.imageDir(this.imageName), {
					recursive: true,
				});
			}
			if (!fs.existsSync(imagePath)) {
				imageBuffer = await this.downloadImage(url);
				logger.info(`saving image to ${imagePath}`);
				fs.writeFileSync(imagePath, imageBuffer);
			} else {
				logger.info(`${imagePath} existed, reading`);
				imageBuffer = fs.readFileSync(imagePath);
			}

			return imageBuffer;
		} else {
			return this.downloadImage(url);
		}
	}

	async renderImageRun(
		child: Child,
		markDefs: MarkDef[]
	): Promise<ImageRun | ExternalHyperlink> {
		const markDef = getMarkTypeByType("imagelink", markDefs);
		return this.imageRun(markDef.href!, child.text);
	}

	async renderTextRun(
		child: Child,
		markDefs: MarkDef[]
	): Promise<TextRun | ExternalHyperlink> {
		let hyperlink: string | undefined = undefined;
		let style = {};
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
				let mark_type = getMarkTypeByKey(mark, markDefs);
				switch (mark_type._type) {
					case "link":
						Object.assign(style, { style: "Hyperlink" });
						hyperlink = urlize(mark_type.href!, this.baseUri).href;
						break;

					default:
						break;
				}
			}
		}
		return this.textRun(child.text, hyperlink, style);
	}

	async renderRun(child: Child, markDefs: MarkDef[]): Promise<RunType> {
		if (isImageRun(child, markDefs)) {
			return this.renderImageRun(child, markDefs);
		} else {
			return this.renderTextRun(child, markDefs);
		}
	}

	async renderBody(
		body: Body,
		styleMap: Map<string, HeadingLevel>
	): Promise<Paragraph> {
		let runs: RunType[] = [];
		for (const child of body.children) {
			runs.push(await this.renderRun(child, body.markDefs));
		}
		const style = makeParagraphStyle(body.style!, styleMap);
		const spacing = inferParagraphSpacing(style);
		return new Paragraph({
			children: runs,
			...style,
			alignment: AlignmentType.JUSTIFIED,
			spacing: {
				after: spacing,
				before: spacing,
				line: 300,
				lineRule: LineRuleType.EXACT,
			},
		});
	}

	async renderBodies(bodies: Body[]): Promise<Paragraph[]> {
		let paragraphs: Paragraph[] = [];
		const headingMap = inferRelativeHeadingMap(bodies);
		const references = inferReference(bodies);

		for (const body of bodies) {
			paragraphs.push(await this.renderBody(body, headingMap));
		}
		return paragraphs;
	}

	renderListString(strings: string[]) {
		return this.textParagraph(strings.join(","));
	}

	renderArticleUrls(articleUrls: ArticleUrl[]) {
		let paragraphs: Paragraph[] = [];
		for (const article of articleUrls) {
			paragraphs.push(
				this.textParagraph(article.urlTitle, article.urlField)
			);
		}
		return paragraphs;
	}

	renderSlug(slug: Slug) {
		return this.textParagraph(slug.current);
	}

	async renderImageUrls(imageUrls: ImageUrl[]) {
		let paragraphs: Paragraph[] = [];
		for (const image of imageUrls) {
			paragraphs.push(
				await this.imageParagraph(image.urlField, image.urlTitle)
			);
		}
		return paragraphs;
	}

	textParagraph(
		text?: string,
		link?: string,
		paraOptions?: IParagraphOptions
	) {
		return new Paragraph({
			...paraOptions,
			children: [this.textRun(text, link)],
		});
	}

	textRun(
		text?: string,
		link?: string,
		runOptions?: IRunOptions
	): TextRun | ExternalHyperlink {
		const run = new TextRun({
			...runOptions,
			text: text ? text : "",
			font: this.fontFamily,
			size: this.fontSize,
			style: link ? "Hyperlink" : undefined,
		});
		return link
			? new ExternalHyperlink({
					children: [run],
					link: urlize(link!, this.baseUri).href,
			  })
			: run;
	}

	async imageRun(href: string, text?: string) {
		let imageBuffer: Buffer = await this.getImageBuffer(href);

		const dims = sizeOf(imageBuffer);
		const [width, height] = transformSize(
			dims.height,
			dims.width,
			this.imageScale
		);
		const imageRun = new ImageRun({
			data: imageBuffer,
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
			altText: {
				title: text!,
				name: text!,
				description: text!,
			},
		});
		this.imageCount += 1;
		return new ExternalHyperlink({
			children: [imageRun],
			link: urlize(href, this.imageUri).href,
		});
	}

	async imageParagraph(href: string, text?: string) {
		return new Paragraph({ children: [await this.imageRun(href, text)] });
	}

	async tableRow(name: string, children: Paragraph[]) {
		const row = new TableRow({
			children: [
				new TableCell({
					children: [this.textParagraph(name)],
					width: { size: 15, type: WidthType.PERCENTAGE },
				}),
				new TableCell({
					children: children,
					width: { size: 85, type: WidthType.PERCENTAGE },
				}),
			],
		});
		return row;
	}

	imageDir(name: string): string {
		return path.join(this.config.imageDir, this.docType, name);
	}

	get fieldMap() {
		return FieldStringMap;
	}
	get docType(): string {
		return this.config.docType;
	}

	get imageName(): string {
		return this._imageName;
	}

	set imageName(name: string) {
		this._imageName = name;
	}

	async renderSenction(doc: DocType) {
		let children: (Paragraph | Table)[] = [
			await this.renderFontMatter(doc),
		];

		return children;
	}

	async run(title?: string): Promise<void> {
		let docs: DocType[] = [];
		const sanity = this.service.get_sanity(true);
		if (title) {
			logger.info(`fetching ${title} json from sanity`);
			docs.push(await sanity.get_document(this.docType, title));
		} else {
			logger.info(`fetching ${this.docType} jsons from sanity`);
			docs.push(...(await sanity.get_documents(this.docType)));
		}
		for (const doc of docs) {
			await this.render(doc);
		}
	}

	save(title: string, children: (Paragraph | Table)[]) {
		const docx = new Document({
			sections: [{ properties: {}, children: children }],
		});
		const filedir = path.join(this.config.outputDir, this.docType);
		const filepath = path.join(filedir, title);

		if (!fs.existsSync(filedir)) {
			fs.mkdirSync(filedir, { recursive: true });
		}

		Packer.toBuffer(docx).then((buffer) => {
			fs.writeFileSync(`${filepath}.docx`, buffer);
		});
	}

	async render(doc: DocType) {
		logger.info(`rendering ${doc.title!}`);
		this.imageCount = 0;
		const children = await this.renderSenction(doc);

		this.save(doc.title!, children);
	}
}
