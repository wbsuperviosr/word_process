import { Body, Slug, BaseDocument } from "./base";

export interface About extends BaseDocument {
	body?: Body;
	footer?: string[];
	mainImageUrl?: string;
	quote?: string;
	slug: Slug;
	subtitle?: string;
	title: string;
}
