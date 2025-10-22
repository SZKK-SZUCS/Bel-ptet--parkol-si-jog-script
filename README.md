<h1 align="center">Welcome to Beléptető parkolási jog script 👋</h1>
<p>
  <img alt="Version" src="https://img.shields.io/badge/version-1-blue.svg?cacheSeconds=2592000" />
</p>

### 🏠 [Homepage](teszt.py)

## Install

```sh
pip install selenium

git clone https://github.com/yourname/belepteto-script.git
cd belepteto-script
```

## Futatás elötti lépések:

### 1. Töltsd fel a mappába az exceled

Fontos: az alábbi oszlop nevek kellenek:

**kartya, jog, rendszam**

Ha több jog vagy rendszám van akkor külön oszlopba legyen és fűzz mögé egy számot, pl.: jog2, rendszam2

### 2. Futtasd a read-excel.js-t

line6: Meg kell adnod az excel elérési útvonalát (Relative path)

line8: Meg kell adnod az új fájl nevét (főleg fontos ha több excelen futtatod le)

### 3. Line 27-28: Add meg a címtáras belépési adataid

### 4. Line 52: Add meg az új json file elérési útvonalát (Relative path)

## Run

```sh
python teszt.py
```

## Author

👤 **Szabó Máté - szabma3**

- Github: [@szmate2003](https://github.com/szmate2003)

## Show your support

Give a ⭐️ if this project helped you!

---

_This README was generated with ❤️ by [readme-md-generator](https://github.com/kefranabg/readme-md-generator)_
