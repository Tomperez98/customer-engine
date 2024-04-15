import {useEffect, useState} from 'react'
import {BASE_URL} from '@/constants/url'
import {useKindeBrowserClient} from '@kinde-oss/kinde-auth-nextjs'

const useGetUnmatchedPrompts = (id?: string) => {
    const [data, setData] = useState<any>()
    const [isLoading, setIsLoading] = useState<boolean>(false)
    const {accessTokenEncoded} = useKindeBrowserClient()

    const url = `${BASE_URL}/unmatched-prompts`

    const fetchUnmatchedPrompts = async () => {
        if (!accessTokenEncoded) return
        const headers = {
            Authorization: `Bearer ${accessTokenEncoded}`,
        }
        setIsLoading(true)

        try {
            const res = await fetch(url, {
                headers: headers,
            })
            const resJson = await res.json()

            setData(resJson)
        } catch (error) {
            console.log(error)
        } finally {
            setIsLoading(false)
        }
    }

    useEffect(() => {
        if (accessTokenEncoded) {
            fetchUnmatchedPrompts()
        }
    }, [accessTokenEncoded])

    const refetch = () => {
        fetchUnmatchedPrompts()
    }

    return {data, isLoading, refetch}
}

export default useGetUnmatchedPrompts
