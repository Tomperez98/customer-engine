import classNames from 'classnames'
import {motion} from 'framer-motion'

interface IconButtonProps {
    Icon: any
    onClick: () => void
    disabled?: boolean
    fill?: string
    size?: string
}

const IconButton = ({disabled, fill, Icon, size, onClick}: IconButtonProps) => {
    const animationProps = disabled
        ? {}
        : {
              whileHover: {scale: 1.1},
              whileTap: {scale: 0.9},
          }
    return (
        <motion.button
            className={classNames(
                fill || 'text-neutral-800 hover:text-cyan-400',
                size || 'text-sm'
            )}
            onClick={onClick}
            {...animationProps}>
            <Icon />
        </motion.button>
    )
}

export default IconButton
