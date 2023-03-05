import { Rumor } from "../models/rumor";
import { Service } from "../service";
import { DocxCore, IDocxConfig } from "./core";

export class RumorEngine extends DocxCore {
	constructor(public config: IDocxConfig, public service: Service) {
		super(config, service);
	}

	async render(doc: Rumor): Promise<void> {
		this.imageName = doc.title;
		super.render(doc);
	}

	get imageInFM() {
		return true;
	}
	get bodyInFM() {
		return true;
	}
}
