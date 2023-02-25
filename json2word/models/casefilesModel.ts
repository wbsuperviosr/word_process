export interface Child {
	_key: string;
	_type: string;
	marks: any[];
	text: string;
}

export interface Body {
	_key: string;
	_type: string;
	children: Child[];
	markDefs: any[];
	style: string;
	level?: number;
	listItem: string;
}

export interface ImageUrl {
	_key: string;
	_type: string;
	urlField: string;
	url_title: string;
	height?: string;
	width?: string;
}

export interface Slug {
	_type: string;
	current: string;
}

export interface Related {
	title: string;
	urlField: string;
	category: string;
}

export interface CaseFile {
	_createdAt: Date;
	_id: string;
	_rev: string;
	_type: string;
	_updatedAt: Date;
	body: Body[];
	classification: string;
	description: string;
	featured: boolean;
	header: string;
	order?: number;
	image_urls: ImageUrl[];
	imageonly: boolean;
	mainImageUrl: string;
	publishedAt: Date;
	slug: Slug;
	title: string;
	tags?: string[];
	writtenAt: Date;
	related?: Related[];
}
