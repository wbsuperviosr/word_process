export interface RumorImage {
	_key: string;
	_type: string;
	urlField: string;
	url_title: string;
	width?: string;
	height?: string;
}

export interface RumorPost {
	_key: string;
	_type: string;
	urlField: string;
	url_title: string;
}

export interface Rumor {
	_createdAt: Date;
	_id: string;
	_rev: string;
	_type: string;
	_updatedAt: Date;
	author: string;
	importance: number;
	question: string;
	rumor: string;
	rumor_images: RumorImage[];
	rumor_posts: RumorPost[];
	rumor_spreader: string[];
	rumor_victim: string[];
	tags: string[];
	truth: string;
	truth_images: RumorImage[];
	truth_posts: RumorPost[];
}
