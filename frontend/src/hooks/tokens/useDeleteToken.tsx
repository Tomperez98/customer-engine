import {useState} from 'react'
import {BASE_URL} from '@/constants/url'
import {useKindeBrowserClient} from '@kinde-oss/kinde-auth-nextjs'

const useDeleteToken = () => {
    const [isLoading, setIsLoading] = useState(false)
    const [error, setError] = useState(null)
    const {accessTokenEncoded} = useKindeBrowserClient()

    console.log(accessTokenEncoded)

    const deleteToken = async () => {
        const headers = {
            Authorization: `Bearer ${accessTokenEncoded}`,
        }
        setIsLoading(true)
        setError(null)
        try {
            const response = await fetch(`${BASE_URL}/whatsapp-tokens`, {
                method: 'DELETE',
                headers: headers,
            })
            setIsLoading(false)
            if (!response.ok) {
                throw new Error('Failed to delete form')
            }
            return await response.json()
        } catch (error: any) {
            setError(
                error.message || 'An error occurred while deleting the form'
            )
            setIsLoading(false)
            throw error
        }
    }

    return {deleteToken, isLoading, error}
}

export default useDeleteToken
