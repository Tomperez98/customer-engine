import {useState} from 'react'
import {BASE_URL} from '@/constants/url'
import {useKindeBrowserClient} from '@kinde-oss/kinde-auth-nextjs'

const useDeleteForm = () => {
    const [isLoading, setIsLoading] = useState(false)
    const [error, setError] = useState(null)
    const {organization} = useKindeBrowserClient()

    const deleteForm = async (id: string) => {
        setIsLoading(true)
        setError(null)
        try {
            const response = await fetch(`${BASE_URL}/${organization}/${id}`, {
                method: 'DELETE',
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

    return {deleteForm, isLoading, error}
}

export default useDeleteForm
