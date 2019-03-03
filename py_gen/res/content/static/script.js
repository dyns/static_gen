
const CTHEME = 'theme'
const LIGHT = 'LIGHT'
const DARK = 'DARK'

const getTheme = () => {
    let lightTheme = Cookies.get(CTHEME)
    if (lightTheme === undefined){
        Cookies.set(CTHEME, LIGHT);
        lightTheme = LIGHT
    }
    return lightTheme
}

const saveTheme = (theme) => {
    Cookies.set(CTHEME, theme)
}

const setThemeBasedOnCookies = () => {
    let lightTheme = getTheme() == LIGHT
    lightThemeCSS.disabled = !lightTheme
    darkThemeCSS.disabled = lightTheme
}

window.onload = () => {
    let lightTheme = getTheme()

    // try to find theme switch
    const themeSwitchId = 'themeBtn'
    const themeToggle = document.getElementById(themeSwitchId)
    const bkgnd = document.getElementsByTagName("BODY")[0];

    const lightThemeCSS = document.getElementById('lightThemeCSS')
    const darkThemeCSS = document.getElementById('darkThemeCSS')

    lightThemeCSS.disabled = true
    darkThemeCSS.disabled = true

    // if found and toggled, toggle theme
    if(themeToggle && bkgnd){
        const darkTxt = 'Dark'
        const lightTxt = 'Light'

        const domThemeSet = () => {
            saveTheme(lightTheme)
            if(lightTheme === LIGHT){
                themeToggle.innerHTML = darkTxt
                lightThemeCSS.disabled = false
                darkThemeCSS.disabled = true
            } else {
                themeToggle.innerHTML = lightTxt
                lightThemeCSS.disabled = true
                darkThemeCSS.disabled = false
            }
        }

        domThemeSet()

        themeToggle.addEventListener('click', () => {
            if(lightTheme === LIGHT){
                lightTheme = DARK
            } else {
                lightTheme = LIGHT
            }
            domThemeSet()
        }) 
    }
}

// call before html loaded to set right css before body drawn
setThemeBasedOnCookies()


