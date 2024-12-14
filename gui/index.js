const COLORS = [];
for (let i = 0; i < 128; i++){
    COLORS.push([0,0,0])
}
const beforeclose = (event) => {event.preventDefault()};
window.addEventListener("beforeunload", beforeclose);
eel.expose(exportColors);

async function apply() {
    await eel.submit_colors()();
    window.removeEventListener("beforeunload",beforeclose);
    alert("Applying changes... You might need to enter your sudo password to continue.")
    close();
}
// region HELPER FUNCTIONS
function hexToRgb(hex) {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? [
        parseInt(result[1], 16),
        parseInt(result[2], 16),
        parseInt(result[3], 16)
    ] : null;
}
function rgbToHex([r,g,b]) {
    // Ensure each value is within the valid range [0, 255]
    r = Math.max(0, Math.min(255, r));
    g = Math.max(0, Math.min(255, g));
    b = Math.max(0, Math.min(255, b));

    // Convert each value to a 2-digit hexadecimal string
    const toHex = (value) => {
        const hex = value.toString(16);
        return hex.length === 1 ? '0' + hex : hex;
    };

    // Concatenate the hexadecimal strings for the final hex color code
    return `#${toHex(r)}${toHex(g)}${toHex(b)}`;
}
function hasBadContrastWithWhite(hexColor) {
    function relativeLuminance([r, g, b]) {
        const [R, G, B] = [r, g, b].map(channel => {
            const sRGB = channel / 255;
            return sRGB <= 0.03928 ? sRGB / 12.92 : Math.pow((sRGB + 0.055) / 1.055, 2.4);
        });
        return 0.2126 * R + 0.7152 * G + 0.0722 * B;
    }
    function contrastRatio(lum1, lum2) {
        return (Math.max(lum1, lum2) + 0.05) / (Math.min(lum1, lum2) + 0.05);
    }

    const rgb = hexToRgb(hexColor);
    const lumColor = relativeLuminance(rgb);
    const lumWhite = relativeLuminance([255, 255, 255]);
    const ratio = contrastRatio(lumColor, lumWhite);

    return ratio < 4.5;
}

function exportColors(){
    let exp = "";
    for (let i = 0; i < 128; i++){
        const rgb = COLORS[i];
        exp += `${rgb[0]},${rgb[1]},${rgb[2]};`
    }
    return exp.substring(0, exp.length - 1);
}

function importColors(colorString){
    const colorElements = colorString.split(";");
    if (colorElements.length !== 128){
        console.error("Too short")
        return false;
    }
    for (let i = 0; i < 128; i++){
        COLORS[i] = colorElements[i].split(",");
        const btn = document.querySelector(`button[data-index='${i}']`);
        if (btn && btn.style){
            btn.style.backgroundColor = rgbToHex(COLORS[i]);
        }
    }
    console.log(COLORS)
}
// endregion

document.addEventListener("DOMContentLoaded", () => {
    const kbContainer = document.getElementById("keyboardContainer");
    // region POPUPS
    const popupContainer = document.getElementById("popups");
    // region EXPORT/IMPORT POPUP
    let exportName = "custom-preset"
    const exportImportPopup = document.getElementById("importPopup");
    const exportImportButton = document.getElementById("exOrImport");
    const exportImportClick = () => {
        popupContainer.style.display = "block";
        exportImportPopup.style.display = "flex";
        const expqrt = document.getElementById("export")
        expqrt.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(exportColors()));
        expqrt.setAttribute('download', exportName);
        function handleSubmit(e) {
            e.preventDefault();
            const file = document.getElementById("import").files[0];
            if (file) {
                const reader = new FileReader();
                reader.fileName = file.name;
                reader.readAsText(file, "UTF-8");
                reader.onload = function (evt) {
                    exportName = evt.target.fileName;
                    importColors(evt.target.result);
                }
                reader.onerror = function () {
                    document.getElementById("import").innerHTML = "error reading file";
                }
            }
            exportImportPopup.dispatchEvent(new Event("reset"));
            exportImportPopup.removeEventListener("submit", handleSubmit);
        }
        exportImportPopup.addEventListener("submit", handleSubmit);
    }

    exportImportButton.addEventListener("click", exportImportClick);

    exportImportPopup.addEventListener("reset", () => {
        popupContainer.style.display = "none";
        exportImportPopup.style.display = "none";
    });
    // endregion
    // region COLOR POPUP
    const colorPopup = document.getElementById("colorPopup");
    const colorInput = document.getElementById("color");

    function openColorPopup(buttonsArr, color = "#000000") {
        console.log(buttonsArr)
        popupContainer.style.display = "block";
        colorPopup.style.display = "flex";

        if (color !== "#000000"){
            const result = /^rgb\((\d{1,3}), (\d{1,3}), (\d{1,3})\)$/i.exec(color);
            colorInput.value = result? rgbToHex([result[1],result[2],result[3]]) : color;
        }

        function handleSubmit(e) {
            e.preventDefault();
            const colorVal = colorInput.value;
            const hasBadContrast = hasBadContrastWithWhite(colorVal);
            for (const button of buttonsArr) {
                console.log(button.textContent)
                button.style.backgroundColor = colorVal;
                if (hasBadContrast){
                    button.style.color = "black";
                }
                else{
                    button.style.color = "";
                }
                const idx = parseInt(button.dataset.index);
                if (isNaN(idx)) {
                    continue;
                }
                COLORS[idx] = hexToRgb(colorVal);
            }
            colorPopup.dispatchEvent(new Event("reset"));
            colorPopup.removeEventListener("submit", handleSubmit);
        }
        colorPopup.addEventListener("submit", handleSubmit);
    }

    colorPopup.addEventListener("reset", () => {
        popupContainer.style.display = "none";
        colorPopup.style.display = "none";
        let active = document.getElementsByClassName("active");
        Array.from(active).forEach(element => {
            element.classList.remove("active");
        });
    });
    
    // endregion
    // region PRESET POPUP TODO
    const presetPopup = document.getElementById("presetPopup");
    const presetButton = document.getElementById("presetNr");
    const presetClick = () => {
        popupContainer.style.display = "block";
        presetPopup.style.display = "flex";
        function handleSubmit(e) {

            presetPopup.dispatchEvent(new Event("reset"));
            presetPopup.removeEventListener("submit", handleSubmit);
        }
        presetPopup.addEventListener("submit", handleSubmit);
    }

    presetButton.addEventListener("click", presetClick);

    presetPopup.addEventListener("reset", () => {
        popupContainer.style.display = "none";
        presetPopup.style.display = "none";
    });

    // endregion
    // region ACTIONS
    document.getElementById("apply").addEventListener("click", apply);
    const buttons = kbContainer.getElementsByTagName("button");
    for (const button of buttons){
        button.addEventListener("click", (evt) => {
            evt.target.classList.toggle("active")
        });

        button.addEventListener("contextmenu", (evt) => {

            openColorPopup([evt.target], evt.target.style.backgroundColor);
            evt.preventDefault();
        });
    }
    const set = document.getElementById("set");
    set.addEventListener("click", () => {
        let active = document.getElementsByClassName("active");
        if (active.length === 0){
            if (!confirm("No selection was made. Do you want to color all buttons?")){
                return;
            }
            active = kbContainer.getElementsByTagName("button");
        }
        openColorPopup(active);
    })

    // endregion
})