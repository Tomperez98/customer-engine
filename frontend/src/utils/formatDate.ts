export const formatDate = (dateString: string): string => {
    const date = new Date(dateString)
    const userLanguage = navigator.language || 'en-US'
    return date.toLocaleString(userLanguage, {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
    })
}
