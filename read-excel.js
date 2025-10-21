import XLSX from "xlsx";
import fs from "fs";
import path from "path";

// TODO: add meg az excel path-et a relative path kimásolásával
const excelPath = path.resolve("UniFamulusParkolás.xlsx");
const outputPath = path.resolve("./parkolas.json");

try {
  const fileBuffer = fs.readFileSync(excelPath);
  const workbook = XLSX.read(fileBuffer, { type: "buffer" });
  const sheetName = workbook.SheetNames[0];
  const worksheet = workbook.Sheets[sheetName];
  const jsonData = XLSX.utils.sheet_to_json(worksheet);
  fs.writeFileSync(outputPath, JSON.stringify(jsonData, null, 2), "utf-8");
  console.log(`✅ JSON sikeresen mentve ide: ${outputPath}`);
} catch (err) {
  console.error("Hiba Excel betöltésekor vagy JSON írásakor:", err.message);
}
