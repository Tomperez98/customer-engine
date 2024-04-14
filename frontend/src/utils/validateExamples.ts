export const validateFieldChange = (
    initialValue: string,
    currentValue: string
) => initialValue === currentValue

export const validateNoEmptyField = (value: string) => Boolean(value.trim())

export const validateNoEmptyFields = (list: string[]): boolean => {
    return list.every((element: string) => element.trim())
}

export const validateAllEmptyFields = (list: string[]): boolean => {
    return list.every((element: string) => !element.trim())
}
