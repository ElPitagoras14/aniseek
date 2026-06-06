export interface StorageItem {
	id: string;
	title: string;
	size: number;
}

export interface StorageResponse {
	items: StorageItem[];
	total: number;
	totalSize: number;
}
