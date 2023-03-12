import { Media } from "../models/media";
import { Service } from "../service";
import { DocxCore, IDocxConfig } from "./core";

export class RumorEngine extends DocxCore {
	constructor(public config: IDocxConfig, public service: Service) {
		super(config, service);
	}

	async render(doc: Media): Promise<void> {
		this.imageName = doc.title;
		super.render(doc);
	}

	get hasFootnote() {
		return false;
	}

	get imageInFM() {
		return true;
	}
	get bodyInFM() {
		return true;
	}
}
