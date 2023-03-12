import { BaseDocument, ArticleUrl, ImageUrl } from "./base";

export interface Rumor extends BaseDocument {
	author?: string;
	importance?: number;
	rumorSpreader?: string[];
	rumorVictim?: string[];

	rumor: Body;
	rumorArticleUrls?: ArticleUrl[];
	rumorImageUrls?: ImageUrl[];

	tags?: string[];
	title: string;

	truth: Body;
	truthArticleUrls?: ArticleUrl[];
	truthImageUrls?: ImageUrl[];
}
