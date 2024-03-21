import {Template} from '@/types/Inputs'

const flattenObject = (obj: Template): string[] => {
    return ([] as string[]).concat(
        ...Object.values(obj).map((val) => (Array.isArray(val) ? val : [val]))
    )
}

export const validateNoEmptyFields = (form: Template): boolean => {
    const objValuesArr = flattenObject(form)
    return objValuesArr.every((element: any) => element.trim())
}

export const validateAllEmptyFields = (form: Template): boolean => {
    const objValuesArr = flattenObject(form)
    return objValuesArr.every((element: any) => !element.trim())
}

export const validateFormHasChanges = (form1: Template, form2: Template) => {
    const flattenedTemplate = flattenObject(form1)
    const flattenedOriginal = flattenObject(form2)

    return !flattenedTemplate.every(
        (element, idx) => element === flattenedOriginal[idx]
    )
}
