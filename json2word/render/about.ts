import { Service } from "../service";
import { DocxCore, IDocxConfig } from "./core";

export class AboutEngine extends DocxCore {
	constructor(public config: IDocxConfig, public service: Service) {
		super(config, service);
	}

	get imageInFM() {
		return false;
	}
	get bodyInFM() {
		return true;
	}
}
