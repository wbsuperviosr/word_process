
export interface Slug {
    _type: string;
    current: string;
}

export interface Subcategory {
    _id: string;
    order?: number|null;
    slug: Slug;
    title: string;
}

export interface Category {
    _id: string;
    slug: Slug;
    subcategory?: Subcategory[];
    title: string;
}