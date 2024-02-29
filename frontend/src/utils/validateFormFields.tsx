export const validateFormFields = (
    currentValue: string,
    originalValue: string
) => {
    const hasChanges = currentValue !== originalValue
    const notEmpty = !currentValue.trim()

    return hasChanges && notEmpty
}
