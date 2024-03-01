import {FormTemplate} from '@/types/Forms'

const flattenObject = (obj: FormTemplate): string[] => {
    return ([] as string[]).concat(
        ...Object.values(obj).map((val) => (Array.isArray(val) ? val : [val]))
    )
}

export const validateNoEmptyFields = (form: FormTemplate): boolean => {
    const objValuesArr = flattenObject(form)
    return objValuesArr.every((element: any) => element.trim())
}

export const validateFormHasChanges = (
    form1: FormTemplate,
    form2: FormTemplate
) => {
    const flattenedTemplate = flattenObject(form1)
    const flattenedOriginal = flattenObject(form2)

    return !flattenedTemplate.every(
        (element, idx) => element === flattenedOriginal[idx]
    )
}
