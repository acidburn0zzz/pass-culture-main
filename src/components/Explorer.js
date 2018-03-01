import React, { Component } from 'react'
import { findDOMNode } from 'react-dom'
import { Carousel } from 'react-responsive-carousel'

import Card from './Card'
import LastCard from './LastCard'
import LoadingCard from './LoadingCard'
import SearchInput from '../components/SearchInput'

class Explorer extends Component {
  componentDidMount () {
    const newState = {
      carouselElement: this.carouselElement,
      carousselNode: findDOMNode(this.carouselElement),
    }
    if (Object.keys(newState).length > 0) {
      this.setState(newState)
    }
  }
  render () {
    const { cards,
      firstCard,
      lastCard,
      loadingTag,
      searchCollectionName,
      searchHook,
      selectedItem
    } = this.props
    console.log('render', selectedItem, cards, 'firstCard', firstCard, 'lastCard', lastCard)
    return (
      <div className='explorer mx-auto p2' id='explorer'>
        <div className='explorer__search absolute'>
          <SearchInput collectionName={searchCollectionName}
            hook={searchHook} />
        </div>
        <Carousel axis='horizontal'
          emulateTouch
          ref={element => this.carouselElement = element}
          selectedItem={selectedItem}
          showArrows={true}
          swipeScrollTolerance={100}
          showStatus={false}
          showIndicators={false}
          showThumbs={false}
          transitionTime={250}
          onChange={this.onChange} >
          {
            loadingTag !== 'search' && cards && cards.length > 0
              ? ((!firstCard && [<LoadingCard key='first' isForceActive />]) || [])
                .concat(
                  cards.map((card, index) =>
                    <Card {...this.state}
                      index={index}
                      itemsCount={cards.length}
                      key={index}
                      {...card} />
                  )).concat([
                    lastCard
                      ? <LastCard key='last' />
                      : <LoadingCard key='next' isForceActive />
                  ])
              : <LoadingCard />
          }
        </Carousel>
      </div>
    )
  }
}

export default Explorer
