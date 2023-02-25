import { Paragraph, TableCell, TableRow, TextRun, WidthType } from "docx";

export function makeTwoColumnsRow(
	name: string,
	children: Paragraph[],
	fontFamily: string = "Microsoft YaHei",
	fontSize: number = 20
) {
	const row = new TableRow({
		children: [
			new TableCell({
				children: [
					new Paragraph({
						children: [
							new TextRun({
								text: name,
								font: fontFamily,
								size: fontSize,
							}),
						],
					}),
				],
				width: { size: 15, type: WidthType.PERCENTAGE },
			}),
			new TableCell({
				children: children,
				width: { size: 85, type: WidthType.PERCENTAGE },
			}),
		],
	});
	return row;
}
