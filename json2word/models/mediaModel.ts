export interface Child {
	_key: string;
	_type: string;
	marks: any[];
	text: string;
}

export interface Content {
	_key: string;
	_type: string;
	children: Child[];
	markDefs: any[];
	style: string;
}

export interface Slug {
	_type: string;
	current: string;
}

export interface Media {
	_createdAt: Date;
	_id: string;
	_rev: string;
	_type: string;
	_updatedAt: Date;
	category: string;
	content: Content[];
	mediaUrl: string;
	imageUrl?: string;
	publishedAt: Date;
	slug: Slug;
	subtitle: string;
	tags: string[];
	title: string;
	writtenAt: Date;
	description: string;
}
