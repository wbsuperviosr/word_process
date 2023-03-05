const fs = require("fs");
import fetch from "cross-fetch";

export async function downloadImageHTTP(
	basedir: string,
	link: string,
	target_name: string
) {
	const savePath = `${basedir}/${target_name}`;
	try {
		if (fs.existsSync(savePath)) {
			console.log(`existed ${savePath}, skip`);
			return;
		}
	} catch (err: any) {
		console.log(err);
	}
	try {
		console.log(`Downloading ${savePath}`);
		const response = await fetch(link);
		const blob = await response.blob();
		const arrayBuffer = await blob.arrayBuffer();
		const buffer = Buffer.from(arrayBuffer);
		await fs.writeFile(savePath, buffer, "binary", function (err: any) {
			if (err) throw err;
		});

		// const raw = await response.body.read();
		// const buf = Buffer.from(raw, "base64");
		// await fs.writeFileSync(savePath, buf, "binary", function (err: any) {
		// 	if (err) throw err;
		// });
		// await response.body.pipe(fs.createWriteStream(savePath));
		await new Promise((r) => setTimeout(r, 2000));
	} catch (error: any) {
		console.log(error);
	}
}
