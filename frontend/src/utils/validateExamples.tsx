export const validateNoEmptyFields = (list: string[]): boolean => {
    return list.every((element: any) => element.trim())
}

export const validateAllEmptyFields = (list: string[]): boolean => {
    return list.every((element: any) => !element.trim())
}
