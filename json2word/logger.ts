import { createLogger, format, transports } from "winston";

const { combine, timestamp, label, printf } = format;

const myFormat = printf(({ level, message, label, timestamp }) => {
	return `${timestamp} [${label}] ${level.toUpperCase()}: ${message}`;
});

export const logger = createLogger({
	format: combine(
		label({ label: "TS Engine" }),
		timestamp({ format: "YYYY-MM-DD hh:mm:ss" }),
		myFormat
	),
	level: "debug",
	transports: [new transports.Console()],
});
