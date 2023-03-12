import { Paragraph, Table } from "docx";
import { Casefile } from "../models/casefile";
import { Service } from "../service";
import { DocxCore, IDocxConfig } from "./core";

export class CasefileEngine extends DocxCore {
	constructor(public config: IDocxConfig, public service: Service) {
		super(config, service);
	}

	async renderSenction(doc: Casefile): Promise<(Table | Paragraph)[]> {
		this.imageName = doc.title;
		let children: (Paragraph | Table)[] = [
			await this.renderFontMatter(doc),
		];

		children.push(...(await this.renderBodies(doc.body)));
		children.push(...(await this.renderImageUrls(doc.imageUrls!)));
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
