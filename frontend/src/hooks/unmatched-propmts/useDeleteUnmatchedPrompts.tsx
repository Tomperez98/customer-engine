import {useState} from 'react'
import {BASE_URL} from '@/constants/url'
import {useKindeBrowserClient} from '@kinde-oss/kinde-auth-nextjs'

const useDeleteUnmatchedPrompts = () => {
    const [isLoading, setIsLoading] = useState(false)
    const [error, setError] = useState(null)
    const {accessTokenEncoded} = useKindeBrowserClient()

    const deleteUnmatchedPrompts = async (id?: string) => {
        const headers = {
            Authorization: `Bearer ${accessTokenEncoded}`,
        }
        const url = id
            ? `${BASE_URL}/unmatched-prompts/${id}`
            : `${BASE_URL}/unmatched-prompts`

        setIsLoading(true)
        setError(null)

        try {
            const response = await fetch(url, {
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

    return {deleteUnmatchedPrompts, isLoading, error}
}

export default useDeleteUnmatchedPrompts
