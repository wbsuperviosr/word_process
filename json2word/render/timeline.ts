import { AlignmentType, HeadingLevel, LineRuleType, Table } from "docx";
import { Service } from "../service";
import { Timeline } from "../models/timeline";
import { DocxCore, IDocxConfig } from "./core";

export class TimelineEngine extends DocxCore {
	currentDate: string = "";

	constructor(public config: IDocxConfig, public service: Service) {
		super(config, service);
	}

	addHeading(date: string) {
		if (date != this.currentDate) {
			this.currentDate = date;
			return this.textParagraph(date, undefined, {
				heading: HeadingLevel.HEADING_1,
				alignment: AlignmentType.JUSTIFIED,
				spacing: {
					after: 300,
					before: 300,
					line: 300,
					lineRule: LineRuleType.EXACT,
				},
			});
		} else {
			return this.textParagraph("", undefined, {
				spacing: {
					after: 300,
					before: 300,
					line: 300,
					lineRule: LineRuleType.EXACT,
				},
			});
		}
	}

	async run(title?: string | undefined): Promise<void> {
		const sanity = this.service.get_sanity(true);
		const docs: Timeline[] = await sanity.get_documents("timeline");
		docs.sort((a, b) => a.order! - b.order!);
		let tables: Table[] = [];
		for (const doc of docs.slice(0, 50)) {
			this.imageCount = 0;
			this.imageName = `${doc.title?.slice(0, 15)}`;
			tables.push(
				this.addHeading(doc.date!),
				...(await this.renderSenction(doc))
			);
			// await sleep(1);
		}
		this.save("时间线", {}, tables);
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
