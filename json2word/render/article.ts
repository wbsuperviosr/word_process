import { Paragraph, Table } from "docx";
import { Article } from "../models/article";
import { Service } from "../service";
import { DocxCore, IDocxConfig } from "./core";

export class ArticleEngine extends DocxCore {
	constructor(public config: IDocxConfig, public service: Service) {
		super(config, service);
	}

	async renderSenction(doc: Article): Promise<(Table | Paragraph)[]> {
		this.imageName = doc.title;
		let children: (Paragraph | Table)[] = [
			await this.renderFontMatter(doc),
		];

		children.push(...(await this.renderBodies(doc.body!)));
		return children;
	}

	get hasFootnote() {
		return true;
	}

	get imageInFM() {
		return false;
	}
	get bodyInFM() {
		return false;
	}
}
